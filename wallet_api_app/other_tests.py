
def tranx_id_generator():
    file = open('wallet_api_app/counter.txt', 'r')
    content = file.read()

    tranx_id = int(content) + 1
    file = open('wallet_api_app/counter.txt', 'w')
    file.write(str(tranx_id))
    file = open('wallet_api_app/counter.txt', 'r')
    content = file.read()
    print(content)
    return content


