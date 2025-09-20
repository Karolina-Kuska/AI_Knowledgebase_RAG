using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using System.Net.Http;
using WebApp.Chat.Client.Extensions;
using WebApp.Chat.Client.Providers;
using WebApp.Chat.Client.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);

var fastApiBase = builder.Configuration["FastApiBaseUrl"] ?? "http://localhost:8000";
var fastApiKey = builder.Configuration["FastApiKey"] ?? "";
var aspApiBase = builder.Configuration["AspApiBaseUrl"] ?? "https://localhost:7029"; // Change to your ASP.NET Core server port


builder.Services.AddHttpClient("FastApi", client =>
{
    client.BaseAddress = new Uri(fastApiBase);
    if (!string.IsNullOrEmpty(fastApiKey))
        client.DefaultRequestHeaders.Add("x-api-key", fastApiKey);
});


builder.Services.AddHttpClient("AspApi", client =>
{
    client.BaseAddress = new Uri(aspApiBase);
});

builder.Services.AddScoped<AuthenticationStateProvider, JwtAuthStateProvider>();
builder.Services.AddScoped(sp => sp.GetRequiredService<IHttpClientFactory>().CreateClient("FastApi"));

builder.Services.AddAuthorizationCore();
builder.Services.AddDependencies();

await builder.Build().RunAsync();
