import babel from "@rollup/plugin-babel";
import commonjs from "@rollup/plugin-commonjs";
import image from "@rollup/plugin-image";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import postcss from "rollup-plugin-postcss";
import { terser } from "rollup-plugin-terser";
import typescript from "@rollup/plugin-typescript";
import external from 'rollup-plugin-peer-deps-external';

export default [
  {
    input: "src/stories/index.tsx",
    output: [
      {
        file: "dist/index.js",
        format: "esm",
        sourcemap: true,
        // name: 'bytebrain-ui'
      },
    ],
    plugins: [
      external(),
      postcss({
        plugins: [],
        minimize: false,
      }),
      nodeResolve({
        extensions: [".js", ".jsx", ".css"],
      }),
      image(),
      babel({
        babelHelpers: "bundled",
        exclude: "node_modules/**",
        presets: ["@babel/preset-react"],
      }),
      commonjs(),
      typescript(),
      terser(),
    ],
    external: ["react", "react-dom", "react-markdown", "highlight.js"],
  },
];
