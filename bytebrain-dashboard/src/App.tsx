import { ModeToggle } from "@/components/mode-toggle";
import { ThemeProvider } from "@/components/theme-provider";
import { Button } from "@/components/ui/button";
import './App.css';

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <div className="text-foreground">
          <p>
            Hello
          </p>
          <Button>Click Here!</Button>
          <ModeToggle />
        </div>
      </ThemeProvider>
    </>
  )
}

export default App
