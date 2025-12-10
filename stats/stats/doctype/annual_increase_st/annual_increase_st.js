// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Increase ST", {
  refresh_employees(frm) {
    frappe.db.get_list("Employee", {
      fields: ['name','custom_sub_department', 'department' , 'grade' , 'custom_step'],
      filters: {
        status: "Active"
      }
    }).then(r => {
      if(r.length < 1) {
        frappe.throw(__("No employees found"));
      }
        frm.clear_table("employees");

      r.forEach(employee => {
        console.log(employee.custom_step,"--------------")

        // add employees to employees table
        console.log(employee,"--------------")
        let row = frm.add_child("employees");
        row.employee = employee.name;
        row.department = employee.department;
        row.sub_department = employee.custom_sub_department;
        row.current_grade = employee.grade;
        row.current_step = employee.custom_step;

        console.log(employee,"--------------")
        // frm.set_value("employees", );
      });
      frm.refresh_field("employees");
      frappe.msgprint(__("Employees list updated"));
    })
  },
  fill_next_step(frm , cdt , cdn) {
    console.log(cdt, cdn,"--------------")
    console.log(frm.doc.employees,"--------------")

    const employee = frm.get_doc("employees", cdn);
      console.log(employee,"--------------")

    const next_step = employee.current_step + 1;
    if(!isNaN(next_step)) {
      return;
    }
    const next_step_doc = frappe.db.get_doc("Step ST", next_step);
    console.log(next_step_doc,"--------------")

    // frm.get_table_rows("employees").forEach(employee => {

    //   const next_step = employee.current_step + 1;
    //   const next_step_doc = frappe.db.get_value("Step ST", next_step);


    //   if(next_step_doc) {
    //     // let row = frm.get_row("employees", employee.name);
    //     // row.new_step = next_step_doc.step;
    //     // row.new_grade = next_grade_doc.grade;
    //     // frm.refresh_field("employees");
    //   }else {
    //     // next_grade = employee.grade + 1;
    //     // next_grade_doc = frappe.db.get_value("Employee Grade", next_grade)
    //     // .then(r => {
    //     // if(next_grade_doc) {
    //     //   first_step_doc = frappe.db.get_value("Step ST", 1);
    //     //   let row = frm.get_row("employees", employee.name);
    //     //   row.new_step = first_step_doc.step;
    //     //   row.new_grade = next_grade_doc.grade;
    //     //   // frm.refresh_field("employees");
    //     // }
    //     // })
    //   }

    //   const grade = frappe.db.get_value("Employee Grade", employee.grade);
    //   console.log(grade,"--------------")
    // });
  }

});
