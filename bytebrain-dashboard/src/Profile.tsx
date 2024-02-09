/**
 * Copyright 2023-2024 ByteBrain AI
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useEffect } from 'react';
import React from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuShortcut
} from "@/components/ui/dropdown-menu"
import { Result } from './authentication/components/signup-form';
import { Button } from './components/ui/button';

type User = {
  full_name: string;
  username: string;
  email: string;
}

function Profile() {
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


  async function setData<T>(fetchCallback: () => Promise<Result<T>>, setCallback: (arg0: T) => any) {
    const data = await fetchCallback();
    if (data.success) {
      setCallback(data.data);
    } else {
      if (data.error === 'Unauthorized') {
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
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Button variant="outline">{userData.full_name}</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{userData.full_name}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {userData.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Subscription</DropdownMenuItem>
        <DropdownMenuItem  onClick={logout}>
          Log out
          <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu >
  )
}

function logout() {
  localStorage.removeItem("accessToken");
  window.location.assign(
    "http://localhost:5173/auth/login"
  );
}

export default Profile