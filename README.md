# hexconv

This is WIP. 

While reading up on IPv6 it struck me that the format that was chosen for addesses (39 characters in most cases) was needlessly long and unwieldy. Wouldn't base32 be better suited for the job? You don't really trade anything in terms of readibility. Especially if you choose the Crockford's variety - it's just a bunch of additional letters. And it **should** be a lot shorter.

But how shorter exactly? And thus this little script was born.