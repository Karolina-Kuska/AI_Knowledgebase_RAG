using System.Runtime.CompilerServices;

namespace WebApp.Chat.Client.Extensions
{
    public static class DependencyInjectionExtension
    {
        public static IServiceCollection AddDependencies(this IServiceCollection services)
        {
            services.AddScoped<Services.SessionService>();
            services.AddScoped<Services.ChatApiClient>();
            return services;
        }
    }
}
