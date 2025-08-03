from marshmallow import Schema, fields, validate, ValidationError

class UserCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=100))
    email = fields.Email(validate=validate.Length(max=255))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))

class SearchSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

def validate_user_id(user_id):
    try:
        user_id_int = int(user_id)
        if user_id_int <= 0:
            raise ValueError("User ID must be a positive integer")
        return user_id_int
    except ValueError:
        raise ValidationError("Invalid user ID format")
