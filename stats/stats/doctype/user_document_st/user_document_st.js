// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("User Document ST", {
	refresh: function (frm) {
        frm.toggle_display("preview", false);

        frm.trigger("preview_file");
    },
    preview_file: function (frm) {
        console.log("Helloo")
		let $preview = "";
		// let file_extension = frm.doc.file_type.toLowerCase();

		if (frappe.utils.is_image_file(frm.doc.file_url)) {
			$preview = $(`<div class="img_preview">
				<img
					class="img-responsive"
					src="${frappe.utils.escape_html(frm.doc.file_url)}"
					onerror="${frm.toggle_display("preview", false)}"
				/>
			</div>`);
		} else if (frappe.utils.is_video_file(frm.doc.file_url)) {
			$preview = $(`<div class="img_preview">
				<video width="480" height="320" controls>
					<source src="${frappe.utils.escape_html(frm.doc.file_url)}">
					${__("Your browser does not support the video element.")}
				</video>
			</div>`);
		} 
        // else if (file_extension === "pdf") {
		// 	$preview = $(`<div class="img_preview">
		// 		<object style="background:#323639;" width="100%">
		// 			<embed
		// 				style="background:#323639;"
		// 				width="100%"
		// 				height="1190"
		// 				src="${frappe.utils.escape_html(frm.doc.file_url)}" type="application/pdf"
		// 			>
		// 		</object>
		// 	</div>`);
		// } else if (file_extension === "mp3") {
		// 	$preview = $(`<div class="img_preview">
		// 		<audio width="480" height="60" controls>
		// 			<source src="${frappe.utils.escape_html(frm.doc.file_url)}" type="audio/mpeg">
		// 			${__("Your browser does not support the audio element.")}
		// 		</audio >
		// 	</div>`);
		// }

		if ($preview) {
			frm.toggle_display("preview", true);
			frm.get_field("preview_html").$wrapper.html($preview);
		}
	},
});
