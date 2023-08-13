import React, { useState } from 'react';
import PopupChatWindow from './PopupChatWindow';

export const ChatApp = (props) => {
  const [isOpen, setIsOpen] = useState(false)
  const close = () => setIsOpen(false)
  const open = () => setIsOpen(true)

  return (
    <div className='bg-blue-400 bg-opacity-30 flex flex-row'>

      <div className='py-3'>
        <button
          id='chat-button'
          className='fixed bg-orange-400 rounded-t-md text-white px-3 py-2 hover:scale-95 transition text-xl bottom-0 right-0'
          onClick={open}
        >
          ZIO Chat!
        </button>
      </div>

      <div className='max-w-3xl mx-auto'>
        <p className='text-lg'>

          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam eget mauris quam. Suspendisse aliquet ornare ligula a rhoncus. Donec laoreet feugiat vestibulum. Quisque id accumsan leo, at tristique tortor. Aliquam ut facilisis ex. Nam pretium ut nunc sit amet fermentum. Aliquam pharetra mauris eget lorem tincidunt molestie. Nunc aliquam risus quis risus bibendum volutpat. Donec efficitur arcu id neque dignissim, condimentum commodo odio eleifend. Quisque eget convallis sem. Sed sit amet ligula sit amet mi sodales bibendum sed quis diam.

          Maecenas sagittis eleifend sem sed hendrerit. Duis sit amet gravida dui. Proin ut turpis ac nulla imperdiet consectetur. Aliquam erat volutpat. Donec ut odio nisl. Vivamus condimentum massa ut ligula placerat, sit amet varius risus vehicula. Mauris vulputate ullamcorper varius. Cras vulputate, velit a faucibus viverra, est velit dapibus magna, vel sagittis arcu turpis vitae metus. Vestibulum a mi eget turpis tincidunt scelerisque vitae quis lectus. Fusce augue urna, ultrices eget ante quis, bibendum malesuada dui. Proin auctor risus sed dolor pellentesque, in vestibulum turpis ornare. Curabitur suscipit risus vitae condimentum semper. Nunc non rutrum mauris. Nunc sed ornare velit. In vel maximus purus. Mauris fringilla est eu dolor ultrices gravida.

          Curabitur ultricies est et rutrum pulvinar. Vestibulum quis lorem nunc. Morbi auctor pellentesque justo nec interdum. Cras non ornare ligula. Fusce massa purus, facilisis sit amet sollicitudin ac, congue quis risus. Aliquam porttitor augue at dui auctor, quis rutrum libero ornare. Donec nulla nunc, rutrum ut tincidunt eget, venenatis id dui. Curabitur vitae nunc vitae felis sagittis accumsan. Suspendisse sit amet venenatis arcu, non convallis nisi. Integer nec leo auctor, placerat mi nec, ultrices lorem. Ut pellentesque ex sed scelerisque pharetra.

          Nunc id molestie purus. Quisque ac nunc sed odio accumsan imperdiet at nec sem. Morbi ligula est, dignissim vitae diam non, pretium vestibulum nisl. Donec consequat diam vel elit placerat pretium. In a nibh neque. Aenean non lacus a risus dapibus porta. Etiam at varius nisl. In sollicitudin imperdiet felis sed volutpat. Pellentesque suscipit ornare vulputate. Pellentesque finibus facilisis nulla a egestas. Pellentesque quis eleifend odio, quis rhoncus elit. Pellentesque ultricies id mauris ut volutpat. Curabitur vitae ante placerat, gravida nisl quis, consectetur erat.

          Morbi luctus orci a velit euismod facilisis. Sed quis consectetur mauris. Vestibulum laoreet consectetur lorem, et blandit ante condimentum vitae. Proin commodo elementum dui, et posuere ex interdum tristique. Sed elementum sagittis dolor, malesuada consequat arcu placerat in. Pellentesque finibus libero in eros luctus dapibus. Donec non elit ac neque scelerisque ultricies. In quis venenatis erat. Nulla facilisi. Duis sit amet volutpat sem, quis vestibulum diam.

          Nunc non velit ac arcu dignissim eleifend. Vestibulum quam leo, finibus a interdum at, tincidunt sit amet orci. Mauris consectetur metus id consectetur fermentum. Proin non nulla sed nisl malesuada pulvinar quis ac lorem. Cras ac semper felis, in fringilla ex. Aenean in congue justo. Donec vitae aliquet lorem. In sit amet semper purus, sit amet dictum tellus. Nullam vulputate nec risus eget vestibulum. Sed dictum ultricies sapien, quis eleifend neque eleifend at. Fusce mollis ultricies mattis. Ut tristique quis est a dictum.

          Praesent placerat rutrum commodo. Suspendisse orci arcu, consectetur sed hendrerit et, efficitur sed mauris. Integer mi ex, gravida vel tellus quis, varius rhoncus ante. Aliquam eu consequat tortor. Proin tincidunt urna ut nisl dictum, eget efficitur tellus cursus. In varius eros vitae quam pharetra, at rutrum sem aliquam. Aenean facilisis rutrum venenatis. Nunc hendrerit commodo consectetur. Aliquam egestas sem nec est sodales, vel mollis urna maximus. Etiam ultrices metus ut nulla laoreet laoreet. Nam at tempus tellus.

          Integer tincidunt augue cursus purus blandit faucibus. Praesent eget lobortis tortor, at tempor diam. Nunc non eros quis justo tincidunt sagittis. Suspendisse potenti. Phasellus pellentesque feugiat vestibulum. Cras pretium, odio in hendrerit pellentesque, dui dui accumsan dui, id gravida sapien arcu nec risus. Donec sit amet condimentum sem. Integer venenatis cursus velit et pretium.

          Praesent bibendum velit sed ligula pulvinar placerat. Mauris et tempus eros. Fusce viverra odio lacus, ut fermentum mi blandit vel. Donec maximus quis enim ac consequat. Nullam mauris arcu, semper a semper sit amet, maximus nec magna. Fusce ac enim et eros blandit hendrerit. Vivamus pretium suscipit est, non tincidunt elit interdum eu. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Integer at ligula arcu. Proin vehicula porta justo vitae blandit. Curabitur augue augue, feugiat at odio quis, ultricies ullamcorper nulla. Integer ullamcorper lacus sem, sed efficitur erat ornare vitae.

          Nulla cursus risus enim, posuere lacinia dolor sodales quis. Suspendisse efficitur leo ut congue egestas. Etiam nisl nisi, ullamcorper quis felis sed, scelerisque scelerisque mauris. Cras at lorem urna. Sed imperdiet purus at erat vestibulum condimentum. Aliquam tempor tempus mauris ac interdum. Mauris quis tristique lorem. Nunc eu mi eu mi ultrices luctus. Nullam varius erat non massa fermentum mattis. Suspendisse venenatis sapien a leo hendrerit, id condimentum ex elementum. Nam a ipsum et metus suscipit consectetur. Etiam non ex sit amet dolor pellentesque feugiat non non mauris. Integer purus metus, finibus sed porttitor nec, venenatis vitae magna. Quisque auctor congue velit non gravida. Pellentesque non erat at ante faucibus interdum.
        </p>
      </div>
      <PopupChatWindow onClose={close} visible={isOpen} />
    </div>
  );
};

export default ChatApp