using Microsoft.JSInterop;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace WebApp.Chat.Client.Services;

public record ChatRequest(string session_id, string message);
public record SourceItem(string? title, string? source, string? preview);
public record ChatResponse(string answer, string intent, string? engine, List<SourceItem> sources);

public class ChatApiClient
{
    private readonly HttpClient _fastApiClient;
    public ChatApiClient(IHttpClientFactory factory)
    {
        _fastApiClient = factory.CreateClient("FastApi");
    }

    public async Task<ChatResponse?> SendAsync(string sessionId, string message, CancellationToken ct = default)
    {
        var payload = new ChatRequest(session_id: sessionId, message: message);
        using var resp = await _fastApiClient.PostAsJsonAsync("chat", payload, ct);
        resp.EnsureSuccessStatusCode();
        return await resp.Content.ReadFromJsonAsync<ChatResponse>(cancellationToken: ct);
    }

    public async Task ClearAsync(string sessionId, CancellationToken ct = default)
    {
        using var resp = await _fastApiClient.PostAsJsonAsync("chat/clear", new { session_id = sessionId }, ct);
        resp.EnsureSuccessStatusCode();
    }
}
