import babel from "@rollup/plugin-babel";
import commonjs from "@rollup/plugin-commonjs";
import image from "@rollup/plugin-image";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import postcss from "rollup-plugin-postcss";
import { terser } from "rollup-plugin-terser";

export default [
  {
    input: "src/stories/index.js",
    output: [
      {
        file: "dist/index.js",
        format: "esm",
      },
    ],
    plugins: [
      nodeResolve({
        extensions: [".js", ".jsx"],
      }),
      postcss({
        plugins: [],
        minimize: true,
      }),
      image(),
      babel({
        babelHelpers: "bundled",
        exclude: "node_modules/**",
        presets: ["@babel/preset-react"],
      }),
      commonjs(),
      terser()
    ],
    external: ["react", "react-dom", "react-markdown", "highlight.js"],
  },
];
