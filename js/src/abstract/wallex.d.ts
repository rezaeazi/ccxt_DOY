import { implicitReturnType } from '../base/types.js';
import _wallex from '../wallex.js';
interface wallex {
    publicGetV1Markets(params?: {}): Promise<implicitReturnType>;
    publicGetV2TradesSymbol(params?: {}): Promise<implicitReturnType>;
    privateGetV1AccountBalances(params?: {}): Promise<implicitReturnType>;
    privateGetV1AccountOpenOrders(params?: {}): Promise<implicitReturnType>;
    privatePostV1AccountOrders(params?: {}): Promise<implicitReturnType>;
    privateDeleteV1AccountOrders(params?: {}): Promise<implicitReturnType>;
}
declare abstract class wallex extends _wallex {
}
export default wallex;
