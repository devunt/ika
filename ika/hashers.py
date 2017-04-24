from base64 import b64encode
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher, CryptPasswordHasher
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes, force_str, force_text


class PasslibBCryptSHA256PasswordHasher(BCryptSHA256PasswordHasher):
    algorithm = "passlib_bcrypt_sha256"

    def encode(self, password, salt):
        bcrypt = self._load_library()
        if self.digest is not None:
            # Django's bcrypt-sha256 implementation uses `binascii.hexlify`, but passlib uses `base64.b64encode`.
            # https://bitbucket.org/ecollins/passlib/src/849ab1e6b5d4ace4c727a63d4adec928d6d72c13/passlib/handlers/bcrypt.py#bcrypt.py-1001

            # password = binascii.hexlify(self.digest(force_bytes(password)).digest())
            password = b64encode(self.digest(force_bytes(password)).digest())
        else:
            password = force_bytes(password)

        data = bcrypt.hashpw(password, salt)
        return "%s$%s" % (self.algorithm, force_text(data))


class PasslibMD5CryptPasswordHasher(CryptPasswordHasher):
    algorithm = 'passlib_md5_crypt'
    library = ('md5_crypt', 'passlib.hash')

    def encode(self, password, salt):
        md5_crypt = self._load_library().md5_crypt
        assert len(salt) == 2
        data = md5_crypt.hash(force_str(password), salt=salt).split('$')[-1]
        return "%s$%s$%s" % (self.algorithm, salt, data)

    def verify(self, password, encoded):
        md5_crypt = self._load_library().md5_crypt
        algorithm, salt, data = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return constant_time_compare(data, md5_crypt.hash(force_str(password), salt=salt).split('$')[-1])