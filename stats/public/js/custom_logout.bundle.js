document.addEventListener('DOMContentLoaded', () => {
	// Wait for frappe to be initialized
	const onFrappeApplication = () => {
		if (window.frappe?.app) {
			// Override the logout function
			frappe.app.logout = function () {
				var me = this;
				me.logged_out = true;

				return frappe.call({
					method: "stats.auth.on_logout",
					callback: function (r) {
                        console.log(r);
						if (r.exc) {
							return;
						}
                        if (r.message.redirect_url) {
                            console.log(r.message.redirect_url);
                            window.location.href = r.message.redirect_url;
                            
                        }else if (r.message.redirect_url == null){
                            console.log("No redirect_url");
                            me.redirect_to_login();
                            // window.location.href = "/login";
                        }
						
					}
				});
			};

			//  Hide Nav Options
			if (frappe.session.user!="Administrator"){
				$(`a.dropdown-item[href="/app/user-profile"]`).hide();                                     // My Profile
				$(`button[onclick="return frappe.ui.toolbar.route_to_user()"]`).hide()                     // My Settings
				$(`button[onclick="return frappe.ui.toolbar.setup_session_defaults()"]`).hide()            // Session Defaults
				$(`button[onclick="return frappe.ui.toolbar.clear_cache()"]`).hide()                       // Clear Cache
				$(`button[onclick="return frappe.ui.toolbar.view_website()"]`).hide()                      // View Website    
				$(`a.dropdown-item[href="/apps"]`).hide()                                                  // Apps
				$(`button[onclick="return frappe.ui.toolbar.toggle_full_width()"]`).hide()                 // Toggle Full Width
				$(`button[onclick="return new frappe.ui.ThemeSwitcher().show()"]`).hide()                  // Toggle Theme   
			}
		} else {
			// Check again in a moment if frappe isn't ready
			setTimeout(onFrappeApplication, 100);
		}
	};

	onFrappeApplication();
});