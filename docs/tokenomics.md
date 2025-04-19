# BLOG Tokenomics Plan (TestNet Draft)

BLOG Tokenomics Plan (TestNet Draft)

This outlines the tokenomics for the BLOG token (TBLOG for TestNet), powering an AI-driven sports betting platform with bot, community, and group pools on Algorand. It supports a social, collaborative community with longevity (30+ years), avoiding burns and using natural loss for scarcity. Designed for TestNet testing, it’s flexible for MainNet adjustments.

Token Details





Name: BLOG Test Token (TBLOG)



Unit Name: TBLOG



Total Supply: 1,000,000,000 (1 billion)





Reason: Balances abundance for decades of betting and usability for small stakes (300 TBLOG). Tests large supply (vs. 10B) while keeping stakes intuitive (300 TBLOG vs. 3,000). Scalable to 2B or 10B for MainNet if needed.



Longevity: Supports ~166,000 users betting 300 TBLOG each at 50M circulating (5% left) in 30 years, addressing concerns about low supply (e.g., 5M from 100M).



Decimals: 6





Reason: Enables micro-bets (0.000001 TBLOG) and large pools (1,000,000 TBLOG), aligning with pool mechanics (300-1,000 TBLOG stakes).



Network: Algorand TestNet (TestNet-API: https://testnet-api.algonode.cloud)





MainNet Note: Revisit supply (1B, 2B, or 10B) post-TestNet based on user feedback (e.g., stake sizes).

Distribution





Bot Wallet: 10,000 TBLOG (0.001%)





Purpose: Funds bot’s 3 daily bets (300-500 TBLOG each), pool fees (1%), and seeding community/group pools.



Details: Covers ~30 days (3 bets x 500 TBLOG x 30 = 9,000 TBLOG). Held by bot wallet (from BOT_MNEMONIC in .env).



Community Rewards: 300,000,000 TBLOG (30%)





Purpose: Incentivizes bettors in community pools (tiered selection, max 3 days) and group leaders (verified, ≥60% win rate).



Allocation:





Daily Payouts: 1,000 TBLOG/day split among 5 community bettors (e.g., 200 TBLOG each for wins).



Streaks: 500 TBLOG for 3-day community win streak.



Leaderboard: 5,000 TBLOG/month to top 5 bettors (1,000 each).



Reason: Drives Discord engagement, rewarding skill and collaboration (social hub goal, April 8, 2025).



Team/Development: 50,000,000 TBLOG (5%)





Purpose: Mock allocation for future features (NBA data, ML models, mobile app), marketing, team costs.



TestNet: Held by creator wallet, no real use.



MainNet Note: 1-year lock, 25% yearly vesting.



Reserve: 649,990,000 TBLOG (64.999%)





Purpose: Simulates uncirculated tokens for partnerships, exchanges, or extra rewards (e.g., mobile launch).



TestNet: Held by creator wallet (from algokit generate wallet).



MainNet Note: Flexible for scaling, audited for transparency.



Liquidity: 0% (TestNet)





MainNet Note: 10% (100M TBLOG) for exchanges (e.g., Tinyman) to enable TBLOG/ALGO swaps.

Token Utility





Betting: Stake TBLOG in pools.





Examples:





!bot_bet "Suns" "+100" 300: Bot stakes 300 TBLOG.



!community_pool "Celtics" "+110" 400: User leads with 400 TBLOG.



!group_pool "Only1" "Warriors" "+120" 500: Group stakes 500 TBLOG.



Rewards: Earn TBLOG for winning bets, leading pools, streaks, or topping leaderboards.





Examples:





Win community pool: 2x stake + 200 TBLOG bonus.



3-day streak: 500 TBLOG.



Top bettor: 1,000 TBLOG/month.



Future Governance (MainNet):





Hold TBLOG to vote on fees, pool rules, or features.



Reason: Fosters community ownership.



Fees: 1% of pool stakes (TBLOG) to bot wallet.





Example: 1,000 TBLOG pool → 10 TBLOG fee.



Reason: Funds bot operations, aligns with betting_pool.py.

Economic Mechanisms





No Burns:





Reason: Avoids artificial scarcity, relying on natural loss (lost wallets, inactive users) to reduce supply over time.



Estimate: 3% annual loss → 1B to ~400M in 30 years, still supporting ~1.3M users at 300 TBLOG each.



Benefit: Keeps TBLOG in circulation for betting, matching preference for longevity over deflation.



TestNet: No burn code in betting_pool.py. Track bets in blog.db to simulate losses.



MainNet Note: Monitor oversupply; consider lockups (e.g., staking) if needed.



Emission:





Community Rewards: 1,000 TBLOG/day (365,000/year).



Cap: 300M over ~821 years, but TestNet tests 1-2 months.



Reason: Controlled rewards prevent inflation, keep stakes affordable.



Staking (Future, MainNet):





Lock TBLOG for bonus rewards (e.g., 5% APY).



Reason: Encourages holding, stabilizes value without burns.

ASA Roles (Algorand Standard Asset)





Manager: Bot wallet (BOT_MNEMONIC)





Purpose: Updates metadata (e.g., token URL).



Reserve: Creator wallet





Purpose: Holds 649.99M TBLOG (TestNet), simulates uncirculated supply.



Freeze: Disabled





Reason: Avoids user distrust, simplifies MVP.



Clawback: Disabled





Reason: Keeps tokens liquid, aligns with betting freedom.

TestNet Considerations





Supply: 1B TBLOG mimics MainNet but tests usability (300 TBLOG bets).



Rewards: Simulate 1,000 TBLOG/day in blog.db to gauge engagement.



Losses: Track stakes/payouts to estimate natural loss (e.g., unclaimed winnings).



Feedback:





Do 300-1,000 TBLOG stakes feel intuitive?



Are 10,000 TBLOG enough for bot bets?



Should supply scale to 2B or 10B for MainNet?

MainNet Adjustments (Future)





Supply: Evaluate 1B, 2B, or 10B based on TestNet.





1B: ~50M in 30 years, supports betting.



2B: Extra buffer for losses.



10B: Maximum longevity, risks low per-token value.



Liquidity: 10% for exchanges.



Vesting: Team tokens locked 1 year.



Audits: Ensure reserve transparency.

Notes





Vision Alignment: Supports a social betting community (April 8, 2025) with rewards for collaboration, streaks, and skill.



Longevity: 1B supply ensures decades of use, even with 95% loss (50M in 30 years).



Flexibility: TestNet allows tweaking (supply, rewards) before MainNet.



Next Steps: Create TBLOG, test in pools, gather feedback on stakes/rewards.

Last Updated: April 15, 2025
