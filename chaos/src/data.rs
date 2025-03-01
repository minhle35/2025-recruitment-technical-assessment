use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};


#[derive(Debug, Serialize, Deserialize)]
#[serde(untagged)]
pub enum requestDataValue{
    Str(String),
    Int(i32),
}

#[derive(Deserialize, Debug)]
pub struct DataRequest {
    data: Vec<requestDataValue>,
}

#[derive(Serialize)]
pub struct DataResponse {
    string_len: i32,
    int_sum: i32,
}

pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
    // Calculate sums and return response
    let mut string_len = 0;
    let mut int_sum = 0;

    for value in request.data.iter() {
        match value {
            requestDataValue::Str(s) => string_len += s.len() as i32,
            requestDataValue::Int(i) => int_sum += i,
        }
    }

    let response = DataResponse {
        string_len,
        int_sum,
    };

    (StatusCode::OK, Json(response))
}
