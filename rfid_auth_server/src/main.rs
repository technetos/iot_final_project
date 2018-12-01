#![feature(proc_macro_hygiene, decl_macro, custom_derive, custom_attribute)]

#[macro_use]
extern crate serde_derive;

#[macro_use]
extern crate diesel;

mod schema;
use crate::schema::files;

#[macro_use]
extern crate rocket;

use compat_uuid::Uuid;
use heatshield::{logout, policy::Bearer, result::WebResult, token, BASEPATH};
use postgres_resource::*;
use rocket::{http::Status, response::status::Custom};
use rocket_contrib::json;
use rocket_contrib::json::{Json, JsonValue};

use diesel::{
    delete, insert_into, prelude::*, result::Error, update, Associations, FromSqlRow, Identifiable,
    Insertable, Queryable,
};

const RFID_ROUTES: &'static str = "/rfid/v1";

fn main() {
    rocket::ignite()
        .mount(BASEPATH, routes![logout::logout, token::get_token])
        .mount(RFID_ROUTES, routes![get_file, open_door])
        .launch();
}

#[derive(Serialize, Deserialize)]
pub struct FilePayload {
    pub fname: String,
}

#[post("/request_file", format = "application/json", data = "<payload>")]
fn get_file(policy: Bearer, payload: Json<FilePayload>) -> WebResult {
    let file_req = payload.into_inner();
    let files = FileController
        .get_all(Box::new(files::account_id.eq(policy.0.user_token.account_id)))
        .map_err(|_| Custom(Status::NotFound, json!({ "error_message": "Not Found" })))?;

    let res = files.iter()
        .filter(|entry| entry.file.fname == file_req.fname)
        .collect::<Vec<_>>();

    if res.is_empty() {
        Err(Custom(Status::NotFound, json!({"error_message": "Not Found" })))
    } else {
        Ok(json!({"file": res.first().unwrap() }))
    }
}

#[post("/unlock_door", format = "application/json")]
fn open_door(policy: Bearer) -> WebResult {
    println!("Unlocking door");
    Ok(json!({}))
}

#[resource(schema = files, table = "files")]
#[DBVAR = "RFID_AUTH_DB"]
struct File {
    account_id: Uuid,
    fname: String,
    content: String,
}

fn setup_mock_data(account_id: Uuid) {
    match FileController
        .create(&File { account_id, fname: String::from("foo.txt"), content: String::from("some random file contents, kyle why arent you paying attention, foobar")})
        .map_err(|_| json!({"error": "unable to create entry"})) {
            Ok(_) => {},
            Err(e) => { println!("{:#?}", e) },
        }
}

