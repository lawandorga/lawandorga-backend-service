def test_password_set(db, mail_user):
    assert mail_user.pw_hash == ""
    mail_user.set_password("pass1234")
    assert mail_user.pw_hash != ""
