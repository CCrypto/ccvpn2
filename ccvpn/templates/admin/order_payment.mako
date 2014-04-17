% if item.payment:
<pre>
% for key, value in item.payment.items():
${key}: ${value}
% endfor
</pre>
% endif

