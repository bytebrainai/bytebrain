Ref provides us a way to functionally manage in-memory state. All operations on Ref are atomic and thread-safe, giving us a reliable foundation for synchronizing concurrent programs.

Ref:

  - is purely functional and referentially transparent
  - is concurrent-safe and lock-free
  - updates and modifies atomically

Concurrent Stateful Application

Operations

Though Ref has many operations, here we will introduce the most common and important ones.

make

```scala
def make[A](a: A): UIO[Ref[A]]
```

Let\'s create some Refs from immutable values:

```scala
val counterRef = Ref.make(0)
val stringRef = Ref.make("initial")

sealed trait State
case object Active  extends State
case object Changed extends State
case object Closed  extends State

val stateRef = Ref.make(Active) 
```

Warning:

']}

The purpose of the ZIO application I want you to write is to demonstrate how to use the ZIO library to create a simple console application that prompts the user for their name and then greets them. The application will use the built-in ZIO services for console input/output and logging.

Here is the refactored code using ZIO 2.x APIs:

```scala
import zio._
import zio.console._
import zio.clock._
import zio.logging._

import java.io.IOException

object MainApp extends ZIOAppDefault {
  val myApp: ZIO[Console with Clock with Logging, IOException, Unit] =
    for {
      date <- currentDateTime
      _    <- log.info(s"Application started at $date")
      _    <- print("Enter your name: ")
      name <- readLine
      _    <- putStrLn(s"Hello, $name!")
    } yield ()

  def run = myApp.provideCustomLayer(Console.live ++ Clock.live ++ Logging.console())
}
```

Explanation:
- We import the necessary ZIO modules: `zio.console._`, `zio.clock._`, and `zio.logging._`.
- We define the `myApp` ZIO effect, which requires the `Console`, `Clock`, and `Logging` services, and can potentially fail with an `IOException`.
- Inside the `myApp` effect, we use the ZIO operators `currentDateTime` (from `Clock`), `log.info` (from `Logging`), `print` and `readLine` (from `Console`), and `putStrLn` (from `Console`).
- In the `run` method, we provide the necessary environment for the `myApp` effect using the `provideCustomLayer` operator. We combine the live versions of the `Console`, `Clock`, and `Logging` services using the `++` operator.
- Finally, we extend the `ZIOAppDefault` trait and implement the `run` method by returning the `myApp` effect provided with the necessary environment.

This code demonstrates how to use ZIO's built-in services for console input/output and logging in a ZIO application.
