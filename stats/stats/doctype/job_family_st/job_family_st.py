# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet, get_root_of
from erpnext.utilities.transaction_base import delete_events


class JobFamilyST(NestedSet):
	nsm_parent_field = "parent_job_family_st"

	def autoname(self):
		self.name =self.job_family_st_name

	def validate(self):
		if not self.parent_job_family_st and not frappe.flags.in_test:
			if frappe.db.exists("Job Family ST", _("All Job Families")):
				self.parent_job_family_st = _("All Job Families")				

	def on_update(self):
		if not (frappe.local.flags.ignore_update_nsm or frappe.flags.in_setup_wizard):
			super().on_update()

	def on_trash(self):
		super().on_trash()
		delete_events(self.doctype, self.name)

	@frappe.whitelist()
	def get_competencies_name(self):
		comp = frappe.db.get_all("Competencies Library Details ST",filters={"parent":self.competencies_library}, fields=['competencies_name'])
		comp_list = [i.competencies_name for i in comp]
		print(comp_list,"++++++++++")
		return comp_list

def on_doctype_update():
	frappe.db.add_index("Job Family ST", ["lft", "rgt"])


@frappe.whitelist()
def get_children(doctype, parent=None, job_family_st=None, is_root=False):
	if parent is None or parent == "All Job Families":
		parent = ""

	return frappe.db.sql(
		f"""
		select
			name as value,
			is_group as expandable
		from
			`tabJob Family ST` comp
		where
			ifnull(parent_job_family_st, "")={frappe.db.escape(parent)}
		""",
		as_dict=1,debug=0
	)


@frappe.whitelist()
def add_tree_node():
	from frappe.desk.treeview import make_tree_args

	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_job_family_st == "All Job Families":
		args.parent_job_family_st = None
	frappe.get_doc(args).insert()

@frappe.whitelist()
def get_competencies_details(competencies_library, competencies_name):
	comp = frappe.db.get_all("Competencies Library Details ST",filters={"parent":competencies_library, "competencies_name":competencies_name}, fields=['category','elements','definition'])
	
	print(comp,"++++++++++")
	return comp