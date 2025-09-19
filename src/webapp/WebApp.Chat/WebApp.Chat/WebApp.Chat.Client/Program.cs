using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using WebApp.Chat.Client.Extensions;
using WebApp.Chat.Client.Services;


var builder = WebAssemblyHostBuilder.CreateDefault(args);
 
var apiBase = builder.Configuration["ApiBaseUrl"] ?? "http://localhost:8000";
var apiKey = builder.Configuration["ApiKey"] ?? "";

builder.Services.AddScoped(sp => {
    var http = new HttpClient { BaseAddress = new Uri(apiBase) };
    if (!string.IsNullOrEmpty(apiKey))
        http.DefaultRequestHeaders.Add("x-api-key", apiKey);
    return http;
});


builder.Services.AddDependencies();

await builder.Build().RunAsync();
