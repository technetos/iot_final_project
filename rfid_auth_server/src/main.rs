#![feature(proc_macro_hygiene, decl_macro, custom_derive, custom_attribute)]

#[macro_use]
extern crate serde_derive;

#[macro_use]
extern crate diesel;

mod schema;
use crate::schema::file_keys;

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
        .mount(RFID_ROUTES, routes![get_key])
        .launch();
}

#[derive(Serialize, Deserialize)]
pub struct FileDecryptionPayload {
    pub fname: String,
}

#[post("/request_key", format = "application/json", data = "<payload>")]
fn get_key(policy: Bearer, payload: Json<FileDecryptionPayload>) -> WebResult {
    let decryption_req = payload.into_inner();
    let key = FileKeyController
        .get_all(Box::new(file_keys::account_id.eq(policy.0.user_token.account_id)))
        .map_err(|_| Custom(Status::NotFound, json!({ "error_message": "Not Found" })))?;

    let res = key.iter()
        .filter(|entry| entry.file_key.fname == decryption_req.fname)
        .collect::<Vec<_>>();

    if res.is_empty() {
        Err(Custom(Status::NotFound, json!({"error_message": "Not Found" })))
    } else {
        Ok(json!({"key": res.first().unwrap() }))
    }
}

#[resource(schema = file_keys, table = "file_keys")]
#[DBVAR = "RFID_AUTH_DB"]
struct FileKey {
    account_id: Uuid,
    fname: String,
    key: String,
}

fn setup_mock_data(account_id: Uuid) {
    match FileKeyController
        .create(&FileKey { account_id, fname: String::from("foo.txt"), key: String::from("shhh")})
        .map_err(|_| json!({"error": "unable to create entry"})) {
            Ok(_) => {},
            Err(e) => { println!("{:#?}", e) },
        }
}

