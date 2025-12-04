frappe.treeview_settings["Job Family ST"] = {
	ignore_fields: ["parent_job_family_st"],
	get_tree_nodes: "stats.stats.doctype.job_family_st.job_family_st.get_children",
	add_tree_node: "stats.stats.doctype.job_family_st.job_family_st.add_tree_node",
	breadcrumb: "Stats",
	disable_add_node: true,
	root_label: "All Job Families",
	get_tree_root: false,
	menu_items: [
		{
			label: __("New Job Family"),
			action: function () {
				frappe.new_doc("Job Family ST", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Job Family ST") !== -1',
		},
	],
	onload: function (treeview) {
		treeview.make_tree();
	},
};
