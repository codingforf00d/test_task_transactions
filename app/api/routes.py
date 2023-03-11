from aiohttp import web
from app.models import User, db, Transaction

HASH_SALT = '123'

"""
 Идея: передавать ключи идемпотентности (UUID) с фронта
 и хранить их некоторое время (зависит от вместимости кеша и влияния его размера на скорость работы, обычно сутки).
 По идее нужно использовать KV базу типа редиса, в качестве ключа можно использовать
 ключ идемпотентности, а значение - результат выполнения транзакции для этого ключа.
 Если клиент пытается выполнить транзакцию с существующим ключом, то получит результат уже 
 выполненой транзакции для этого ключа.
"""
idempotence_keys = {}


async def create_user(request: web.Request):
    data = await request.json()
    username = data['username']
    password = hash(data['password'] + HASH_SALT)
    user = await User.create(username=username, password_hash=password)
    return web.json_response({
        'id': user.id,
        'name': user.username,
    })


async def get_user_balance(request: web.Request):
    user_id = request.match_info['id']
    query = db.text("""
    with
    total_withdraw as (select sum(amount) as amount from transactions where from_user = :id),
    total_deposit as (select sum(amount) as amount from transactions where to_user = :id)
    select (total_deposit.amount - total_withdraw.amount) from total_deposit, total_withdraw
    """)
    balance = await db.first(query, id=int(user_id))
    return web.json_response({
        'id': user_id,
        'balance': balance[0] or 0
    })


async def add_transaction(request: web.Request):
    data = await request.json()
    exist_transaction: Transaction = idempotence_keys.get(data['idempotence_key'])
    if exist_transaction is not None:
        return web.json_response(map_transaction_to_json(exist_transaction))
    if data['amount'] < 0:
        raise Exception('amount must be 0 or greater')

    result = await Transaction.create(
            from_user=data['from_user'],
            to_user=data['to_user'],
            amount=data['amount']
    )

    idempotence_keys[data['idempotence_key']] = result
    return web.json_response(map_transaction_to_json(result))


async def get_transaction(request: web.Request):
    txn_id = request.match_info['id']
    txn = await Transaction.get(int(txn_id))
    if txn is None:
        return None

    return web.json_response(map_transaction_to_json(txn))


def add_routes(app):
    app.router.add_route('POST', r'/v1/user', create_user, name='create_user')
    app.router.add_route('GET', r'/v1/user/{id}/balance', get_user_balance, name='get_user')
    app.router.add_route('PUT', r'/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{id}', get_transaction, name='incoming_transaction')


def map_transaction_to_json(txn: Transaction):
    return {
            'id': txn.id,
            'amount': txn.amount,
            'from_user': txn.from_user,
            'to_user': txn.to_user
        }