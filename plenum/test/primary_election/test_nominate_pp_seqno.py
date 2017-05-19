from plenum.test.delayers import ppDelay
from plenum.test.helper import sendReqsToNodesAndVerifySuffReplies, \
    sendRandomRequests
from plenum.test.malicious_behaviors_node import slow_non_primary
from plenum.test.pool_transactions.conftest import looper, clientAndWallet1, \
    client1, wallet1, client1Connected
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change.helper import ensure_view_change
from stp_core.loop.eventually import eventually


def test_nominate_after_timeout(looper, txnPoolNodeSet, client1,
                                wallet1, client1Connected):
    """
    One node lags behind others and has not seen all 3PC messages, hence not
    ordered as many requests as others so it sends Nomination only after the
    timeout for the first one it saw nomination from. Others have ordered same
    number of requests so they all send Nomination as soon as they get one
    """
    delay = 10
    npr = slow_non_primary(txnPoolNodeSet, 0, delay)
    slow_node = npr.node
    sendRandomRequests(wallet1, client1, 5)
    ensure_view_change(looper, txnPoolNodeSet, client1, wallet1)
    ensureElectionsDone(looper, txnPoolNodeSet)

    def chk():
        assert npr.name not in slow_node.elector.nominations[0]

    looper.run(eventually(chk))



def test_reelection_when_nodes_send_different_ledger_summary():
    """
    Delay each node's Nomination such that nodes receive different ledger
    summaries and they do re-election
    :return:
    """
    pass
