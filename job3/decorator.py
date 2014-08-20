import random
import string
import time

hitCount = 0
totalCount = 0

def memoed(fn):
    memo = {}
    def inner(*args):
        global hitCount
        global totalCount

        totalCount += 1
        if args not in memo:
            memo[args] = fn(*args)
        else:
            hitCount += 1
        return memo[args]
    return inner

@memoed
def distance(source, target):
    if not source:
        return len(target)
    if not target:
        return len(source)
    if source[0] == target[0]:
        return distance(source[1:], target[1:])
    return 1 + min(
        distance(source, target[1:]),
        distance(source[1:], target),
        distance(source[1:], target[1:])
    )

def randomString(length):
    maxlength = len(string.ascii_letters + string.digits)
    if(length > maxlength):
        return ''.join(random.sample(string.ascii_letters + string.digits, maxlength)) + randomString(length - maxlength)
    else:
        return ''.join(random.sample(string.ascii_letters + string.digits, length))

source = randomString(30)
target = randomString(30)

tpstart = time.clock()
count = distance(source, target)
tpend = time.clock()

print('From %s to %s takes %s steps and %s s' % (source, target, count, tpend-tpstart))
print(hitCount, totalCount)