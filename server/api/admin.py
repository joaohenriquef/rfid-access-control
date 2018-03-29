from django.contrib import admin
from django import forms
from django.forms import PasswordInput
from django.contrib.auth.models import User as DjangoAdminUser, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from api.models import *

admin.site.site_title = 'Controle de Acesso LASPI'
admin.site.site_header = 'Controle de Acesso LASPI'

class UserCreationForm(forms.ModelForm):
	password_input = forms.CharField(label='Password', widget=forms.PasswordInput)
	password_conf_input = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('first_name','last_name','email', 'cpf','access_level')

	def clean_password_conf_input(self):
		# Check that the two password entries match
		password_input = self.cleaned_data.get("password_input")
		password_conf_input = self.cleaned_data.get("password_conf_input")
		if password_input and password_conf_input and password_input != password_conf_input:
			raise forms.ValidationError("Passwords don't match")
		return password_conf_input

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password_input"])
		if commit:
			user.save()
		return user


class UserChangeForm(forms.ModelForm):
	password_input = forms.CharField(
		label='Password', 
		widget=forms.PasswordInput, 
		required = False, 
		help_text="Leave blank to keep same password")
	password_conf_input = forms.CharField(
		label='Password confirmation', 
		widget=forms.PasswordInput, 
		required = False,
		help_text="Leave blank to keep same password")

	class Meta:
		model = User
		fields = ('first_name','last_name','email', 'cpf','access_level')

	def clean_password_conf_input(self):
		# Check that the two password entries match
		password_input = self.cleaned_data.get("password_input")
		password_conf_input = self.cleaned_data.get("password_conf_input")
		if password_input != password_conf_input:
			raise forms.ValidationError("Passwords don't match")
		return password_conf_input

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super(UserChangeForm, self).save(commit=False)
		if (self.cleaned_data["password_input"] != ""):
			user.set_password(self.cleaned_data["password_input"])
		if commit:
			user.save()
		return user
	
	def clean_date_added(self):
		return self.initial["date_added"]

class RfidTagUserLinkInline(admin.TabularInline):
	model = RfidTagUserLink

class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	form = UserChangeForm
	add_form = UserCreationForm
	inlines = [RfidTagUserLinkInline, ]    

	list_display = ('first_name','last_name','email', 'cpf','access_level')
	list_filter = ('access_level', )
	fieldsets = (
		(None, {'fields': ('first_name','last_name','email', 'cpf','access_level', 'password_input', 'password_conf_input')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('first_name','last_name','email', 'cpf','access_level', 'password_input', 'password_conf_input')}
		),
	)
	search_fields =  ('first_name','last_name','email', 'cpf','access_level',)
	ordering = ()
	filter_horizontal = ()

class EventAdmin(admin.ModelAdmin):
	model = Event
	list_display = ('date','user', 'room', 'event_type', 'reader_position')
	list_filter = ['date','user', 'room', 'event_type', 'reader_position']

	def get_readonly_fields(self, request, obj=None):
		if self.declared_fieldsets:
			fields = flatten_fieldsets(self.declared_fieldsets)
		else:
			form = self.get_formset(request, obj).form
			fields = form.base_fields.keys()
		return fields
	
	def has_add_permission(self, request):
		# Nobody is allowed to add
		return False
	def has_delete_permission(self, request, obj=None):
		# Nobody is allowed to delete
		return False

admin.site.register(User, UserAdmin)        
admin.site.register(Room)
admin.site.register(RfidTag)
admin.site.register(Event, EventAdmin)