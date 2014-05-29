<h3>Bitcoin</h3>
% if btcd:
    <ul>
        <li>Balance: ${btcd.balance}</li>
        <li>Blocks: ${btcd.blocks}</li>
        <li>Difficulty: ${btcd.difficulty}</li>
        <li>Connections: ${btcd.connections}</li>
    </li>
% else:
    <p><b>Failed to connect to the bitcoin daemon.</b></p>
%endif

% if graph:
<h3>Users</h3>
    <figure><embed src="/admin/graph/users.svg?period=m" /></figure>
    <figure><embed src="/admin/graph/users.svg?period=y" /></figure>

<h3>Income<h3>
    <figure><embed src="/admin/graph/income.svg?period=m&amp;currency=eur" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=y&amp;currency=eur" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=m&amp;currency=btc" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=y&amp;currency=btc" /></figure>
% endif
