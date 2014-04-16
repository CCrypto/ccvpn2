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
    <figure><embed src="/admin/graph/income.svg?period=m&amp;method=0" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=y&amp;method=0" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=m&amp;method=1" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=y&amp;method=1" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=m&amp;method=2" /></figure>
    <figure><embed src="/admin/graph/income.svg?period=y&amp;method=2" /></figure>
% endif
