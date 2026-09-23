from common.security import hash_password, verify_password


def test_password_roundtrip():
    encoded = hash_password("Prueba123!", iterations=10_000)
    assert verify_password("Prueba123!", encoded)
    assert not verify_password("incorrecta", encoded)
