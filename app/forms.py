from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField, FileField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, NumberRange, EqualTo, Email
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    # User fields
    phone = IntegerField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    # Store fields
    store_name = StringField('Store Name', validators=[DataRequired()])
    store_address = StringField('Store Address', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    phone2 = IntegerField('Phone 2', validators=[Optional()])
    store_logo = FileField('Store Logo', validators=[Optional()])

    submit = SubmitField('Register')


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    display_picture = FileField("Display Picture", validators=[FileAllowed(['jpg', 'png', 'jpeg']), Optional()])
    images = FileField("Additional Images (can select multiple)", render_kw={"multiple": True}, validators=[FileAllowed(['jpg', 'png', 'jpeg']), Optional()])
    metal_type = SelectField("Metal Type", choices=[("gold", "Gold"), ("silver", "Silver")], validators=[DataRequired()])
    category = SelectField("Category", choices=[('necklaces', 'Necklaces'), ('earrings', 'Earrings'), ('bracelets', 'Bracelets'), ('rings', 'Rings'), ('other', 'Other')], validators=[DataRequired()])
    metal_purity = IntegerField("Metal Purity (1-24)", validators=[DataRequired(), NumberRange(min=1, max=24)])
    metal_quantity = FloatField("Metal Quantity (Tola)", validators=[DataRequired()])
    jarti = FloatField("Jarti (%)", validators=[DataRequired()])
    jyala = FloatField("Jyala (Fixed)", validators=[DataRequired()])
    submit = SubmitField("Save Product")



class ProfileForm(FlaskForm):
    phone = IntegerField("Phone", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    password = PasswordField("New Password", validators=[
        Optional(),
        Length(min=6, message="Password must be at least 6 characters."),
        EqualTo("confirm", message="Passwords must match.")
    ])
    confirm = PasswordField("Confirm New Password")

    store_name = StringField("Store Name", validators=[Optional()])
    store_address = StringField("Store Address", validators=[Optional()])
    latitude = FloatField("Latitude", validators=[Optional()])
    longitude = FloatField("Longitude", validators=[Optional()])
    phone2 = IntegerField("Alternate Phone", validators=[Optional()])
    store_logo = FileField("Store Logo", validators=[
        FileAllowed(['jpg', 'png', 'jpeg']),
        Optional()
    ])

    submit = SubmitField("Update Profile")

class AdminProfileForm(FlaskForm):
    phone = IntegerField("Phone", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    password = PasswordField("New Password", validators=[
        Optional(),
        Length(min=6, message="Password must be at least 6 characters."),
        EqualTo("confirm", message="Passwords must match.")
    ])
    confirm = PasswordField("Confirm New Password")
    submit = SubmitField("Update Profile")

class RateForm(FlaskForm):
    gold_price = FloatField("Gold Price per Tola", validators=[DataRequired()])
    silver_price = FloatField("Silver Price per Tola", validators=[DataRequired()])
    submit = SubmitField("Save Rates")

class ForgotPasswordForm(FlaskForm):
    phone = IntegerField("Phone", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField("Reset Password")