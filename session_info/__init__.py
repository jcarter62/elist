from flask import session


class Session_Info:
    data = {}

    def __init__(self):
        self.get_info()
        return

    def get_info(self):
        user_id = ''
        username = ''
        email = ''
        admin = False

        if 'user_id' in session:
            user_id = session['user_id']
        if 'username' in session:
            username = session['username']
        if 'email' in session:
            email = session['email']
        if 'admin' in session:
            admin = session['admin']

        self.data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'admin': admin
        }
        return

    def matches_id(self, user_id) -> bool:
        result = False
        if 'user_id' in session:
            id = session['user_id']
            if int(id) == int(user_id):
                result = True
        return result


