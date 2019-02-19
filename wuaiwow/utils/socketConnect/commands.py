# coding:utf-8


FIRST = {
    "account": 'account',
    "ban": 'ban',
    "baninfo": 'baninfo',
    "banlist": 'banlist',
    "unban": 'unban',
    "character": 'character',
    "lookup": 'lookup',
    "pinfo": 'pinfo',
    "send": 'send',
}

SECOND = {
    "account": {"create": 'create', "delete": 'delete', "onlinelist":'onlinelist', "set":'set'},
    "ban":{"account":'account', "character":'character', "playeraccount":'playeraccount', "ip":'ip'},
    "baninfo":{"account":'account', "character":'character', "ip":'ip'},
    "banlist":{"account":'account', "character":'character', "ip":'ip'},
    "unban":{"account":'account', "character":'character', "playeraccount":'playeraccount', "ip":'ip'},
    "character":{"customize":'customize', "changefaction":'changefaction', "changerace":'changerace', "deleted":'deleted',
                 "erase":'erase', "level":'level', "rename":'rename', "reputation":'reputation', "title":'title'},
    "lookup":{"area":'area', "creature":'creature', "event":'event', "faction":'faction', "item":'item', "itemset":'itemset',
              "object":'object', "quest":'quest', "player":'player', "skill":'skill', "spell":'spell', "taxinode":'taxinode',
              "tele":'tele', "title":'title', "map":'map'},
    "send":{"mail":'mail', "item":'item', "message":'message', 'money':'money'}
}

THIRD = {
    "set": {"addon": 'addon', "sec":'sec', "gmlevel": 'gmlevel', "password": 'password'},      # account set ...
    "deleted": {"delete": 'delete', "list": 'list', "restore": 'restore', "old": 'old'},       # character deleted ...
    "player": {"ip": 'ip', "account": 'account', "email": 'email'},                            # lookup player...
}

FORTH = {
    "sec":{"regmail":'regmail', "email":'email'},                        # account set sec ...
}