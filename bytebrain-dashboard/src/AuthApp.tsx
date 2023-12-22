import React, { useEffect } from "react";
import "./App.css";

("use client");

const CLIENT_ID = "c9345d9e244bb69e4c59";

function loginWithGithub(): void {
  window.location.assign(
    "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID
  );
}

export function AuthApp() {
  const [rerender, setRerender] = React.useState(false);
  const [userData, setUserData] = React.useState({ name: "guest" });

  useEffect(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const codeParam = urlParams.get("code");
    console.log(codeParam);

    if (codeParam && localStorage.getItem("accessToken") == null) {
      async function getAccessToken() {
        await fetch("http://localhost:8081/getAccessToken?code=" + codeParam, {
          method: "GET",
        })
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            console.log(data);
            if (data.access_token) {
              localStorage.setItem("accessToken", data.access_token);
              getUserData();
              setRerender(!rerender);
            }
          });
      }
      getAccessToken();
    }

    if (!codeParam && localStorage.getItem("accessToken")) {
      getUserData();
    }
  }, []);

  async function getUserData() {
    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      try {
        await fetch("http://localhost:8081/getUserData", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        })
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            setUserData(data);
          });
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        {localStorage.getItem("accessToken") ? (
          <>
            <h1>Hello {userData.name}</h1>
            <button
              onClick={() => {
                localStorage.removeItem("accessToken");
                setRerender(!rerender);
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <button onClick={loginWithGithub}>Login with Github</button>
        )}
      </header>
    </div>
  );
}

export default AuthApp;
