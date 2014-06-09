CCrypto VPN - http://vpn.ccrypto.org/
-------------------------------------

Hello,

% if user.paid_time_left.days > 0:
Your account ${user.username} is going to expire in ${user.paid_days_left()} days.
You can already renew it, the time will be added to your account.
% else:
Your account ${user.username} is expired.
To continue using it, you will need to renew it.
% endif

If you have any question, you can contact us by replying to this email.

