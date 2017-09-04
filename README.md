# hexconv
---
This is WIP (albeit almost finished). 

While reading up on IPv6 it struck me that (**if only we didn't have to stick to octets**) the format that was chosen for addresses (39 characters in most cases) was needlessly long and unwieldy. Wouldn't `base32` be better suited for the job? You don't really trade anything in terms of readibility. Especially if you choose [the Crockford's variety](http://www.crockford.com/wrmg/base32.html "Douglas Crockford's Base32") - it's just a bunch of additional letters. And it **should** be a lot shorter.

But how shorter exactly? Well, I know you just have to divide `128` by `5` `(32 = 2^5)` to see that you need at least `26` characters to express a `128-bit` number space with `base32`, but still to see it clearer I needed some kind of converter. And thus this little script was born.

Ignoring the built-in Python capabilities was intentional.