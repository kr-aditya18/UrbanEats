# contains helper function for our code

def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendordashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl1 = 'custdashboard'
        return redirectUrl1
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        
        return redirectUrl
        