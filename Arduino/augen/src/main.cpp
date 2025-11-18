#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include <Preferences.h>

// Kamera-Pins für AI Thinker
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Globale Variablen
Preferences preferences;
httpd_handle_t camera_httpd = NULL;

framesize_t currentRes = FRAMESIZE_VGA;

// --- Kamera starten ---
void startCamera(framesize_t fs = FRAMESIZE_VGA) {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000; // weniger flackern?
  config.frame_size = fs;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }
  currentRes = fs;
  Serial.println("Kamera erfolgreich gestartet!");
}

// --- Handler: Root ---
esp_err_t root_handler(httpd_req_t *req) {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>ESP32-CAM</title></head><body>";
  html += "<h1>ESP32-CAM</h1>";
  html += "<p><a href='/capture'>Einzelbild</a></p>";
  html += "<p><a href='/stream'>Stream</a></p>";
  html += "<p><a href='/settings'>Kamera-Einstellungen</a></p>";
  html += "<p><a href='/wlan'>WLAN Einstellungen</a></p>";
  html += "</body></html>";
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, html.c_str(), html.length());
}

// --- Handler: Capture ---
esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return ESP_OK;
}

// --- Handler: Stream ---
esp_err_t stream_handler(httpd_req_t *req) {
  static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=frame";
  static const char* _STREAM_BOUNDARY = "\r\n--frame\r\n";
  static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

  httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);

  while (true) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Kamera Capture fehlgeschlagen");
      continue;
    }
    char part_buf[64];
    size_t hlen = snprintf(part_buf, 64, _STREAM_PART, fb->len);
    httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    httpd_resp_send_chunk(req, part_buf, hlen);
    httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
  }
  return ESP_OK;
}

// --- Handler: Settings ---
esp_err_t settings_handler(httpd_req_t *req) {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Einstellungen</title></head><body>";
  html += "<h1>Kamera-Einstellungen</h1>";
  html += "<form action='/apply'>";
  html += "<label>Auflösung:</label>";
  html += "<select name='res'>";
  html += "<option value='10' " + String(currentRes == FRAMESIZE_VGA ? "selected" : "") + ">VGA (640x480)</option>";
  html += "<option value='13' " + String(currentRes == FRAMESIZE_SVGA ? "selected" : "") + ">SVGA (800x600)</option>";
  html += "<option value='15' " + String(currentRes == FRAMESIZE_XGA ? "selected" : "") + ">XGA (1024x768)</option>";
  html += "<option value='20' " + String(currentRes == FRAMESIZE_SXGA ? "selected" : "") + ">SXGA (1280x1024)</option>";
  html += "<option value='22' " + String(currentRes == FRAMESIZE_UXGA ? "selected" : "") + ">UXGA (1600x1200)</option>";
  html += "</select><br><br>";
  html += "<input type='submit' value='Übernehmen'>";
  html += "</form>";
  html += "<p><a href='/'>Zurück</a></p>";
  html += "</body></html>";
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, html.c_str(), html.length());
}

// --- Handler: Apply ---
esp_err_t apply_handler(httpd_req_t *req) {
  char buf[100];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[10];
    if (httpd_query_key_value(buf, "res", param, sizeof(param)) == ESP_OK) {
      int r = atoi(param);
      esp_camera_deinit();
      startCamera((framesize_t)r);
      preferences.begin("camera", false);
      preferences.putInt("res", r);
      preferences.end();
    }
  }
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, "<p>Einstellungen übernommen. <a href='/'>Zurück</a></p>", -1);
}

// --- Handler: WLAN-Seite ---
esp_err_t wlan_handler(httpd_req_t *req) {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>WLAN</title></head><body>";
  html += "<h1>WLAN verbinden</h1>";
  html += "<form action='/wlanSave'>";
  html += "SSID: <input type='text' name='ssid'><br>";
  html += "Passwort: <input type='password' name='pass'><br>";
  html += "<input type='submit' value='Speichern'>";
  html += "</form>";
  html += "<p><a href='/'>Zurück</a></p>";
  html += "</body></html>";
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, html.c_str(), html.length());
}

// --- Handler: WLAN speichern ---
esp_err_t wlanSave_handler(httpd_req_t *req) {
  char buf[100];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char ssid[32], pass[64];
    if (httpd_query_key_value(buf, "ssid", ssid, sizeof(ssid)) == ESP_OK &&
        httpd_query_key_value(buf, "pass", pass, sizeof(pass)) == ESP_OK) {
      preferences.begin("wifi", false);
      preferences.putString("ssid", ssid);
      preferences.putString("pass", pass);
      preferences.end();
      WiFi.begin(ssid, pass);
    }
  }
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, "<p>WLAN gespeichert. Starte neu...</p>", -1);
}

// --- URI Handler Strukturen ---
static httpd_uri_t uri_root      = {"/",       HTTP_GET, root_handler, NULL};
static httpd_uri_t uri_capture   = {"/capture",HTTP_GET, capture_handler, NULL};
static httpd_uri_t uri_stream    = {"/stream", HTTP_GET, stream_handler, NULL};
static httpd_uri_t uri_settings  = {"/settings",HTTP_GET, settings_handler, NULL};
static httpd_uri_t uri_apply     = {"/apply",  HTTP_GET, apply_handler, NULL};
static httpd_uri_t uri_wlan      = {"/wlan",   HTTP_GET, wlan_handler, NULL};
static httpd_uri_t uri_wlanSave  = {"/wlanSave",HTTP_GET, wlanSave_handler, NULL};

// --- Webserver starten ---
void startServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &uri_root);
    httpd_register_uri_handler(camera_httpd, &uri_capture);
    httpd_register_uri_handler(camera_httpd, &uri_stream);
    httpd_register_uri_handler(camera_httpd, &uri_settings);
    httpd_register_uri_handler(camera_httpd, &uri_apply);
    httpd_register_uri_handler(camera_httpd, &uri_wlan);
    httpd_register_uri_handler(camera_httpd, &uri_wlanSave);
  }
}

// --- Setup ---
void setup() {
  Serial.begin(115200);
  preferences.begin("wifi", true);
  String ssid = preferences.getString("ssid", "");
  String pass = preferences.getString("pass", "");
  preferences.end();

  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("ESP32-CAM");
  if (ssid != "") {
    WiFi.begin(ssid.c_str(), pass.c_str());
  }
  Serial.println("AP gestartet: " + WiFi.softAPIP().toString());

  preferences.begin("camera", true);
  int res = preferences.getInt("res", (int)FRAMESIZE_VGA);
  preferences.end();
  startCamera((framesize_t)res);

  startServer();
}

// --- Loop ---
void loop() {}
