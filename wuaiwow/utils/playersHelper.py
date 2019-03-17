# coding: utf-8
import re
import datetime
from wuaiwow import db
from wuaiwow.models import Characters, User


def _get_user_by_name(name):
    user = User.query.filter(User.username == name).first()
    return user


def find_or_create_character(user, chname):
    """
        Find existing character or create new character

        @param user user名或User obj
        @param chname 角色名
    """
    name = chname.strip(' ')
    character = Characters.query.filter(Characters.name == name).first()
    if isinstance(user, basestring):
        user = User.query.filter(User.username == user)
    if not character:
        character = Characters(name=name)
        character.user = user
        db.session.add(character)
    return character


def update_wowaccount(username, data_dict):
    """Characters at account ABC (Id: 10)
         wyyzxml (GUID 0)
         wyyzxml2 (GUID 1)
       TC>
    @param username user名
    @param data_dict 从lserver返回的Response
    @return all characters
    """
    characters = []
    data = data_dict.get('message', None)
    user = _get_user_by_name(name=username)
    if user and data and isinstance(data, basestring):
        pattern1 = re.compile(r'.+\s*\(.*\)')
        pattern2 = re.compile(r'(\w{2,})\s+\(GUID\s*(\d+)\)')
        match_all = pattern1.findall(data)
        for m in match_all:
            if 'GUID' in m:
                match = pattern2.search(m)
                if match:
                    character_name = match.groups()[0]
                    guid = int(match.groups()[1])
                    character = find_or_create_character(user, character_name)
                    character.guid = guid
                    user.characters.append(character)
                    characters.append(character)
        # update account update-time
        user.update_time = datetime.datetime.now()
        db.session.add(user)
        # Save to DB
        db.session.commit()

    return characters


def update_wowaccount_characters(username, data_dict):
    """根据角色名更新信息,message 内容
    │Player  (offline) Bb (guid: 3)
    │ Account: ABC (ID: 10), GMLevel: 0
    │ Last Login: 2016-06-14 00:01:12 (Failed Logins: 0)
    │ OS: Win - Latency: 0 ms
    └ Registration Email:  - Email:
    │ Last IP: 192.168.1.125 (Locked: No)
    │ Level: 1 (0/400 XP (400 XP left))
    │ Race: Female 亡灵, 潜行者
    │ Alive ?: Yes
    │ Money: 0g0s0c
    │ Played time: 0h
    TC>
    @param username user名
    @param data_dict 从lserver返回的Response
    """
    character = {'char': None}
    msg = data_dict.get('message', None)
    if msg and isinstance(msg, basestring):
        fields = msg.split(u'│')
        for field in fields:
            if 'Player' in field:
                pattern = re.compile(r'\)\s+(\w{2,})\s+\(')
                match = pattern.search(field)
                if match:
                    character_name = match.groups()[0]
                    character['char'] = find_or_create_character(username, character_name)
            elif 'Last Login' in field:
                pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                match = pattern.search(field)
                if match:
                    character['char'].last_login = datetime.datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
            elif 'Level' in field:
                pattern = re.compile(r':\s+(\d+)\s+\(')
                match = pattern.search(field)
                if match:
                    character['char'].level = int(match.groups()[0])
            elif 'Race' in field:
                pattern = re.compile(r'\w+:\s+(\w+)\s+(.+),\s+(.+)')
                match = pattern.search(field)
                if match:
                    character['char'].gender = match.groups()[0]
                    character['char'].race = match.groups()[1]
                    character['char'].job = match.groups()[2]
            elif 'Alive' in field:
                pattern = re.compile(r'\w+\W+:\s(\w+)')
                match = pattern.search(field)
                if match:
                    character['char'].alive = match.groups()[0] == 'Yes'
            elif 'Money' in field:
                pattern = re.compile(r'Money:\s+(\d+g\d+s\d+c)')
                match = pattern.search(field)
                if match:
                    character['char'].money = match.groups()[0]
            elif 'Played time' in field:
                pattern = re.compile(r'Played time:\s+(.+)')
                match = pattern.search(field)
                if match:
                    total_time = match.groups()[0]
                    character['char'].played_time = total_time.rstrip()
        if character['char']:
            character['char'].update = datetime.datetime.now()
            db.session.add(character['char'])
            db.session.commit()

    return character['char']
