from plenum.test.helper import sendReqsToNodesAndVerifySuffReplies, \
    checkViewNoForNodes
from plenum.test.malicious_behaviors_node import slow_non_primary
from plenum.test.pool_transactions.conftest import clientAndWallet1, \
    client1, wallet1, client1Connected, looper
from plenum.test.view_change.helper import ensure_view_change


def test_slow_node_start_view_same_pp_seq_no(txnPoolNodeSet, looper,
                                        wallet1, client1, client1Connected,
                                        tconf):
    """
    A slow node starts the new view with same pp_seq_no as other nodes
    """
    old_view_no = checkViewNoForNodes(txnPoolNodeSet)
    delay = 10
    npr = slow_non_primary(txnPoolNodeSet, 0, delay)
    slow_node = npr.node
    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1, 5)
    new_view_no = ensure_view_change(looper, txnPoolNodeSet, client1, wallet1)
    assert new_view_no != old_view_no
    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1, 5)
    for node in txnPoolNodeSet:
        if node != slow_node:
            # Since ordered is indexed by tuple of (view_no, pp_seq_no)
            assert npr.ordered == node.replicas[0].ordered
