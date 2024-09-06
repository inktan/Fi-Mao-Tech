// import axios from "axios"
// import { showMessage } from "@/utils";

// const ins = axios.create(); //  创建一个axios实例
// ins.interceptors.response.use(function (resp) {
    // console.log('拦截器');
    // return resp.data;
    // if (resp.data.code === 0) {
    //     return resp.data.data;
    // }
    // const options = {
    //     content: resp.data.msg,
    //     type: "error",
    //     duration: 2000,
    // container: containerRef.value,
    // callback: function () {
    //     console.log("完成!!!")
    // }
    // }
    // showMessage(options);
    // return null;
// });

// 添加请求拦截器
// ins.interceptors.request.use(function (config) {
// 在发送请求之前做些什么
// console.log('Axios Request Config:', config);
// console.log('Axios Request Config:', config.headers);
// console.log('Request body:', config.data);
// if (config.data instanceof FormData) {
// 遍历FormData对象并打印键值对
//     for (const [key, value] of config.data) {
//         console.log(`${key}:${value}`);
//     }
// }
// return config;

// }, function (error) {
// 对请求错误做些什么
//     console.error('Request error:', error);
//     return Promise.reject(error);
// });

// 添加响应拦截器
// ins.interceptors.response.use(function (response) {
// 对响应数据做点什么
// console.log('Axios Response:', response);
// return response;
// }, function (error) {
// 对响应错误做点什么
// console.error('Axios Error:', error);
// return Promise.reject(error);
// });

// export default ins;
