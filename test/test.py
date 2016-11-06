

if __name__ == '__main__':
    brief = "####a```sdsad###```fsdfs"
    filters = ['`', '#']
    for item in filters:
        brief = brief.replace(item, '')
    print brief