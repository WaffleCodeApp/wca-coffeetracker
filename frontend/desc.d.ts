declare module "*.png";
declare module "*.svg";
declare module "*.md" {
  const content: string;
  export default content;
}
