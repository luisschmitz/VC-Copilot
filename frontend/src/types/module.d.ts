declare module '@/components/*' {
  const component: any;
  export default component;
}

declare module '@/lib/*' {
  const module: any;
  export * from module;
}
