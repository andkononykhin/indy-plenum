import random
from time import perf_counter

from plenum.test import waits
from plenum.test.delayers import ppDelay, delayNonPrimaries, nom_delay, \
    prim_delay, rel_delay
from plenum.test.helper import sendReqsToNodesAndVerifySuffReplies, \
    sendRandomRequests
from plenum.test.malicious_behaviors_node import slow_non_primary
from plenum.test.pool_transactions.conftest import looper, clientAndWallet1, \
    client1, wallet1, client1Connected
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change.helper import ensure_view_change, \
    check_each_node_reaches_same_end_for_view
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually


logger = getlogger()


def test_nominate_after_timeout(looper, txnPoolNodeSet, client1,
                                wallet1, client1Connected):
    """
    One node lags behind others and has not seen all 3PC messages, hence not
    ordered as many requests as others so it sends Nomination only after the
    timeout for the first one it saw nomination from. Others have ordered same
    number of requests so they all send Nomination as soon as they get one
    """
    # Long delay so that election messages reach the node but it is still
    # behind others
    delay = 10
    npr = slow_non_primary(txnPoolNodeSet, 0, delay)
    slow_node = npr.node
    logger.debug('{} will be slow by {}'.format(slow_node, delay))
    sendRandomRequests(wallet1, client1, 10)
    new_view_no = ensure_view_change(looper, txnPoolNodeSet, client1, wallet1)
    ensureElectionsDone(looper, txnPoolNodeSet)

    def chk():
        assert slow_node.elector.nominations[0][npr.name][0] == npr.name

    looper.run(eventually(chk))

    check_each_node_reaches_same_end_for_view(txnPoolNodeSet, new_view_no)
    slow_node.nodeIbStasher.resetDelays()


def test_reelection_when_nodes_send_different_ledger_summary(looper,
                                                             txnPoolNodeSet,
                                                             client1,
                                                             wallet1,
                                                             client1Connected):
    """
    Delay each node's Nomination such that nodes receive different ledger
    summaries and they do re-election
    :return:
    """
    min_delay = 3
    max_delay = 8
    for node in txnPoolNodeSet:
        d = min_delay + random.randint(0, max_delay-min_delay)
        logger.debug('{} will get election with delay {}'.format(node, d))
        node.nodeIbStasher.delay(nom_delay(d, 0))
        node.nodeIbStasher.delay(prim_delay(d, 0))
        node.nodeIbStasher.delay(rel_delay(d, 0))

    before_election_time = perf_counter()
    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1, 5)
    new_view_no = ensure_view_change(looper, txnPoolNodeSet, client1, wallet1)

    def chk():
        for node in txnPoolNodeSet:
            assert [e.params['reelection'] for e in
                           node.elector.spylog.getAll(node.elector.processReelection.__name__)
                           if e.params['reelection'].instId == 0 and e.starttime > before_election_time]
    looper.run(eventually(chk, retryWait=1, timeout=3+3 * 2 * max_delay))
    for node in txnPoolNodeSet:
        node.nodeIbStasher.resetDelays()
    ensureElectionsDone(looper, txnPoolNodeSet)
    check_each_node_reaches_same_end_for_view(txnPoolNodeSet, new_view_no)
    # Check if each node agreed on the same ledger summary and last ordered
    # seq no for same view