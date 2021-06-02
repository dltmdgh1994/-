package com.example.dps;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.example.dps.login.SaveSharedPreference;

import org.json.JSONArray;
import org.json.JSONObject;

import java.security.cert.CertificateException;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import androidx.appcompat.app.AppCompatActivity;
import okhttp3.OkHttpClient;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class DayDriveRiskActivity extends AppCompatActivity {
    Button analysis_page;
    private Intent intent;

    private String user_id;

    JSONObject emotion; // 어제의 감정
    JSONObject sleep; // 어제의 졸음운전

    // 감정
    JSONArray emotion_time;
    JSONArray emotion_emotion;
    int emotion_len;

    // 졸음
    JSONArray sleep_eye;
    int[] eye;
    //retrofit
    Retrofit retrofit;
    RetrofitAPI retrofitAPI;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_day_drive_risk);
        analysis_page=findViewById(R.id.analysis_page);
        // 자동 로그인 여부 확인
        if(SaveSharedPreference.getUserID(DayDriveRiskActivity.this).length() == 0) {
            // call Login Activity
            intent = new Intent(DayDriveRiskActivity.this, MainActivity.class);
            startActivity(intent);
            this.finish();
        } else {
            // 자동 로그인 활성화 되어 있다면
            analysis_page.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    intent = new Intent(DayDriveRiskActivity.this, AnalysisActivity.class);
                    intent.putExtra("user_id", SaveSharedPreference.getUserID(DayDriveRiskActivity.this).toString());
                    startActivity(intent);
                    DayDriveRiskActivity.this.finish();
                }
            });

            user_id = SaveSharedPreference.getUserID(DayDriveRiskActivity.this).toString();
            retrofit = new Retrofit.Builder()
                    .addConverterFactory(GsonConverterFactory.create()) // converter 선언
                    .baseUrl(retrofitAPI.REGIST_URL)
                    .client(getUnsafeOkHttpClient().build())
                    .build();
            retrofitAPI = retrofit.create(RetrofitAPI.class);
            Call<ResponseBody> call = retrofitAPI.getYesterdaydata(user_id);
            call.enqueue(new Callback<ResponseBody>() {
                @Override
                public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                    try {
                        ResponseBody body = response.body();
                        String jsonstr = body.string();
                        JSONObject jsonObj = new JSONObject(jsonstr);
                        emotion = (JSONObject) jsonObj.get("Emotion");
                        sleep = (JSONObject) jsonObj.get("Sleep");

                        System.out.println("sleep: " + sleep);
                        sleep_eye = (JSONArray) sleep.get("0");

                        eye = new int[3];
                        eye[0] = sleep_eye.getInt(0);
                        eye[1] = sleep_eye.getInt(1);
                        eye[2] = sleep_eye.getInt(2);

                        //System.out.println(eye);


                    } catch (Exception e) {
                        e.printStackTrace();
                        System.out.println("JsonObj 오류"); //확인
                    }
                }
                @Override
                public void onFailure(Call<ResponseBody> call, Throwable t) {
                    System.out.println("통신 실패");
                }
            });


        }


    }
    //SSL 인증 없이 HTTPS 통과
    public static OkHttpClient.Builder getUnsafeOkHttpClient() {
        try {
            final TrustManager[] trustAllCerts = new TrustManager[] {
                    new X509TrustManager() {
                        @Override
                        public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType) throws CertificateException {
                        }

                        @Override
                        public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType) throws CertificateException {
                        }

                        @Override
                        public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                            return new java.security.cert.X509Certificate[]{};
                        }
                    }
            };

            final SSLContext sslContext = SSLContext.getInstance("SSL");
            sslContext.init(null, trustAllCerts, new java.security.SecureRandom());

            final SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();

            OkHttpClient.Builder builder = new OkHttpClient.Builder();
            builder.sslSocketFactory(sslSocketFactory, (X509TrustManager)trustAllCerts[0]);
            builder.hostnameVerifier(new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            });
            return builder;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

    }
}