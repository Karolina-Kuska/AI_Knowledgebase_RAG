using Microsoft.JSInterop;

namespace WebApp.Chat.Client.Services;

public class SessionService
{
    private readonly IJSRuntime _js;
    private const string KeyId = "rag_session_id";
    private const string KeyTouched = "rag_session_touched";
    private static readonly TimeSpan Ttl = TimeSpan.FromHours(1);

    public SessionService(IJSRuntime js) { _js = js; }

    public async Task<string> GetOrCreateSessionAsync()
    {
        var id = await _js.InvokeAsync<string>("localStorage.getItem", KeyId);
        var touchedStr = await _js.InvokeAsync<string>("localStorage.getItem", KeyTouched);

        var now = DateTimeOffset.UtcNow;
        if (!string.IsNullOrWhiteSpace(id) && DateTimeOffset.TryParse(touchedStr, out var touched))
        {
            if ((now - touched) < Ttl)
            {
                await TouchAsync();
                return id;
            }
        }

        id = Guid.NewGuid().ToString("N");
        await _js.InvokeVoidAsync("localStorage.setItem", KeyId, id);
        await TouchAsync();
        return id;
    }

    public async Task TouchAsync()
    {
        var now = DateTimeOffset.UtcNow.ToString("o");
        await _js.InvokeVoidAsync("localStorage.setItem", KeyTouched, now);
    }

    public async Task ResetAsync()
    {
        await _js.InvokeVoidAsync("localStorage.removeItem", KeyId);
        await _js.InvokeVoidAsync("localStorage.removeItem", KeyTouched);
    }
}
