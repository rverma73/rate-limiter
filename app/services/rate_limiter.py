import time

from app.database.redis import redis_client


CAPACITY = 10
REFILL_RATE = 10 / 60


TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call("HMGET", key, "tokens", "last_refill")

local tokens = tonumber(data[1])
local last_refill = tonumber(data[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = now - last_refill

tokens = math.min(
    capacity,
    tokens + elapsed * refill_rate
)

if tokens < 1 then
    redis.call(
        "HSET",
        key,
        "tokens", tokens,
        "last_refill", now
    )

    return 0
end

tokens = tokens - 1

redis.call(
    "HSET",
    key,
    "tokens", tokens,
    "last_refill", now
)

return 1
"""


def allow_request(user_id: str) -> bool:

    key = f"rate_limit:{user_id}"

    result = redis_client.eval(
        TOKEN_BUCKET_SCRIPT,
        1,
        key,
        CAPACITY,
        REFILL_RATE,
        time.time()
    )

    return result == 1