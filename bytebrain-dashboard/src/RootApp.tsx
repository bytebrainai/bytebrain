
import React from 'react';

import { useEffect } from 'react';
import { Result } from './authentication/components/signup-form';

export function RootApp() {

  const [rerender, setRerender] = React.useState(false);
  const [userData, setUserData] = React.useState<User>({ 'full_name': 'Guest', 'email': '', 'username': '' });

  useEffect(() => {
    const access_token = localStorage.getItem("accessToken");
    if (access_token) {
      setData(() => getUserData(access_token), setUserData)
    } else {
      window.location.assign(
        "http://localhost:5173/auth/login"
      );
    }
  }, []);


  type User = {
    full_name: string;
    username: string;
    email: string;
  }

  async function setData<T>(fetchCallback: () => Promise<Result<T>>, setCallback: (arg0: T) => any) {
    console.log("nnnnnnnn")
    const data = await fetchCallback();
    if (data.success) {
        console.log("jjjjj")
      setCallback(data.data);
    } else {
        console.log("jjjjjjfffff")
      if (data.error === 'Unauthorized') {
        console.log("ssssss")
        localStorage.removeItem("accessToken");
        window.location.assign(
          "http://localhost:5173/auth/login"
        );
      }
      console.log("Failed to fetch user data:", data.error)
    }
  }

  async function getUserData(access_token: string): Promise<Result<User>> {
    try {
      const response = await fetch("http://localhost:8081/users/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })
      console.log(response, "aaa")
      if (response.ok) {
        const responseData = await response.json();
        return { success: true, data: responseData };
      } else {
        if (response.status === 401) {
          return { success: false, error: 'Unauthorized' }
        }
        return { success: false, error: response };
      }
    } catch (error) {
      console.log(error, "bbb")
      return { success: false, error: error };
    }
  }


  return (
    <div>
      <p>RootApp</p>
      <p>
        Hello {userData.full_name}!
      </p>
    </div>
  )
}

export default RootApp;