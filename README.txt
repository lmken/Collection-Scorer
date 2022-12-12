** 
Created by Luke Kennedy
**

This is an app that will take a Ethereum NFT contract address as input and return a score that reflects how consistent high amounts of liquidity are amongst unique holders.
A multiplier is added for larger communities, as a larger community generally means a more active community. Effectively a market and community research tool, 
this app can be used to discover Ethereum-based NFT collections with the most well-resourced NFT collectors. The application uses JavaScript on the client-side and Python 
with Flask on the server-side to accomplish this task.

IMPORTANT NOTES: 
1.) To use this app locally, a Moralis API key is needed. The free tier is sufficient; one can be acquired from https://moralis.io/nft-api/. Place this in a 'config.py' file, 
set to a variable called MORALIS_API_KEY.
2.) The Moralis API does sometimes experience downtime. This may be a cause for any 500 Errors experienced. Check API uptime on https://status.moralis.io/.
Error codes for this are in the works.
3.) This app currently runs in Python, so there is no parallel processing involved. In order to compute the score of a collection, one API call 
must be made per wallet to retrieve native token balance. As a result, processing of large collections can take a long time. Re-architecting this 
application using a language that supports multi-threading (such as Go) is currently of high priority. For more information during the score computation process 
in these development stages, please refer to the console after clicking 'Submit'. 
4.) For quick and easy testing, here is the contract address to the Pixel Vault Core NFT Collection: 0xFb10b1717C92e9cc2d634080c3c337808408D9E1

TODO:
- Parallel processing for the wallet API calls (potential re-architecture to background processing. Potentially a change in language (Go?))
- Increase error-handling capabilities
- Add a loading animation since it takes time to compute a score.
- Implement a cached "rankings" list of pre-computed collection scores that can be displayed upon page-load. This will
  allow for more context when generating scores. New rankings may be computed and re-cached once per 24h.
- Add logo, banner at the top of site, and other aesthetic touches.
- QoL: Include "history" where, when computing a collection, instead of replacing a already computed value with a new value, just bump the old value down.
- QoL: Capture name of collection and instead of writing "Collection Score: ..." have a fully formed response with Collection Name, Contract address, 
  collection size, # holders, and score.
- Add some more optional analytics that can be requested (i.e. "this collection is in the Xth percentile", scatter plots using matplotlib or an equivalent (maybe), etc.)
- Implement React
