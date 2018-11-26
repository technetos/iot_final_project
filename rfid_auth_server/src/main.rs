#![feature(proc_macro_hygiene, decl_macro, custom_derive, custom_attribute)]
#[macro_use]
extern crate rocket;

use rocket_contrib::json; 

use heatshield::{logout, token, policy::Bearer, result::WebResult, BASEPATH};
const RFID_ROUTES: &'static str = "/rfid/v1";

fn main() {
    rocket::ignite()
        .mount(BASEPATH, routes![logout::logout, token::get_token])
        .mount(RFID_ROUTES, routes![get_key])
        .launch();
}

#[get("/get_key", format = "application/json")]
fn get_key(_policy: Bearer) -> WebResult {
    // todo:
    // setup postgres database with (id, account_id, key)
    Ok(json!({"key": "abc123"}))
}
