import { ReferenceItem } from './References';
import UserTypes from "./UserTypes";

export interface Message {
  userType: UserTypes;
  message: string;
  completed: boolean;
  references?: ReferenceItem[];
}

export default Message;